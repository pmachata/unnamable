def discover_modules (idx):
    # some sort of real module discovery will be here instead

    import mod_ah
    idx.add_module (mod_ah.ModuleProto ())

    import mod_ancient
    idx.add_module (mod_ancient.ModuleProto ())

    import mod_monster
    idx.add_module (mod_monster.ModuleProto ())

    import mod_common
    idx.add_module (mod_common.ModuleProto ())

    import mod_unique
    idx.add_module (mod_unique.ModuleProto ())

    import mod_spell
    idx.add_module (mod_spell.ModuleProto ())

    import mod_skill
    idx.add_module (mod_skill.ModuleProto ())

    import mod_terror
    idx.add_module (mod_terror.ModuleProto ())
